import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import app as service

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(service, 'client', None)
    service.app.config['TESTING'] = True
    return service.app.test_client()


def test_case_selection_is_request_scoped(client):
    first = client.get('/case_info', headers={'X-Model-ID': 'model_01'}).json
    second = client.get('/case_info', headers={'X-Model-ID': 'model_07'}).json
    again = client.get('/case_info', headers={'X-Model-ID': 'model_01'}).json
    assert first == again
    assert first['case_id'] != second['case_id']
    assert second['current_model'] == 'model_07'


@pytest.mark.parametrize('body', [None, [], 'wrong'])
def test_bad_json_rejected(client, body):
    response = client.post('/switch_model', data=json.dumps(body), content_type='application/json')
    assert response.status_code == 400


@pytest.mark.parametrize('model', ['../../', 'model_99', ''])
def test_unknown_case_rejected(client, model):
    assert client.post('/switch_model', json={'model_id': model}).status_code in (400, 404)


def test_no_key_mode(client):
    assert client.get('/health').json['ai_enabled'] is False
    assert client.get('/case_info').status_code == 200
    response = client.post('/chat', json={'question': 'Explain this case'})
    assert response.status_code == 503
    assert 'OPENAI_API_KEY' in response.json['error']


def test_mocked_ai_uses_selected_case(client, monkeypatch):
    create = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='Recorded case explanation.'))]))
    monkeypatch.setattr(service, 'client', SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    result = client.post('/chat', json={'question': 'What changed?'}, headers={'X-Model-ID': 'model_07'})
    assert result.status_code == 200
    assert result.json['answer'] == 'Recorded case explanation.'
    context = create.call_args.kwargs['messages'][-1]['content']
    case = json.loads((ROOT/'backend/data/models/model_07/result.json').read_text())
    assert case['case_name'] in context


def test_invalid_region(client):
    assert client.post('/explain_pressure', json={'zone_name': 'engine'}).status_code == 400
    assert client.get('/region_summary/engine').status_code == 404


@pytest.mark.parametrize('page', ['/', '/shape.html', '/pressure.html', '/drag.html', '/model.html', '/config.js'])
def test_frontend_served(client, page):
    assert client.get(page).status_code == 200


def test_private_files_not_served(client):
    assert client.get('/backend/app.py').status_code == 404
    assert client.get('/.env').status_code == 404


def test_case_artifacts(client):
    models = client.get('/models').json['available_models']
    assert len(models) == 7
    for model in models:
        folder = ROOT/'backend/data/models'/model
        record = json.loads((folder/'result.json').read_text())
        drag = record['drag']
        assert drag['before'] > 0
        assert abs(drag['delta'] - (drag['before']-drag['after'])) < .0011
        assert abs(drag['reduction_percent'] - 100*(drag['before']-drag['after'])/drag['before']) < .1
        for file in ['shape_regions.json', 'pressure_regions.json', 'click_map.json']:
            regions = json.loads((folder/file).read_text())
            assert {x['region_id'] for x in regions} == {'front','roof','side','rear'}
        for image in record['images'].values():
            assert (folder/image).is_file()

### 🌐 Языки

[English](../../README.md) | **Русский**

# GeoAgent

GeoAgent — это встроенный в [GeoView](https://github.com/geo-kit/GeoView) ИИ-помощник, который ускоряет рабочие процессы.

## Что он может делать

| Инструмент | Назначение |
|---|---|
| `find_reservoir_models` | Перечисляет подкаталоги и файлы `.DATA` / `.hdf5` в одном каталоге. Содержимое файлов не читает. |
| `load_model_in_geoview` | Открывает модель в GeoView |
| `run_simulation_in_geoview` | Запускает расчёт средствами симулятора JutulDarcy |
| `prepare_optimization_in_geoview` | Запрашивает и заполняет параметры оптимизации NPV и открывает вкладку Optimization |

## Кинфиденциальность

Агент не может открыть командную оболочку, выполнить код или изменить файл на вашем диске. 
Он читает списки каталогов, а не их содержимое. 
Все, что он записывает, попадает в каталог артефактов GeoView в формате JSON.

## Установка

Агента запускает и останавливает сам GeoView, поэтому шаги установки описаны там:
**[Как включить чат](https://github.com/geo-kit/GeoView/blob/main/translations/ru/README.md#%D0%B2%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%87%D0%B0%D1%82%D0%B0-geoagent)**.

Клонируйте рядом с GeoView — именно туда GeoView смотрит по умолчанию:

```
your-workspace/
├── GeoView/
└── GeoAgent/
```

Любое другое место тоже подойдёт, если на него указывает `GEOVIEW_AGENT_DIR`.

## Настройка

| Переменная | Назначение |
|---|---|
| `GEOAGENT_MODEL` | `provider:model`. Провайдеры: `openai`, `lmstudio`, `ollama`. GeoView устанавливает это из своих собственных флагов. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI или  совместимый с OpenAI протокол. |
| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | Локальный сервер LM Studio. |
| `OLLAMA_BASE_URL` | Ollama. |

Пример настройки — в файле `.env.example`.


## Взаимодействие с GeoView

GeoView и агент являются отдельными процессами и передают работу через общий
каталог, а не через API. Агент записывает команду, а затем публикует указатель на нее:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json # что делать и с чем
<GEOVIEW_RESULT_DIR>/results/latest.json # {"run_id": ...}, записано последним
```

GeoView раз в секунду проверяет указатель и направляет манифест по полю `type`. Указатель
агент пишет последним, поэтому GeoView не подхватит наполовину записанный запрос.

У этого агента `type` — всегда запрос: `load_model`, `run_simulation` или
`optimization_setup`. Результаты он не пишет, потому что сам ничего не считает.

Чтобы добавить новые возможности, заведите новый `type` с обеих сторон.

## Разработка

Нужны Python 3.13 и [uv](https://docs.astral.sh/uv/). Выполните в этой директории:

```bash
uv venv && uv pip install -e . --group dev
pytest
ruff check . && ruff format --check .
```

Чтобы дорабатывать самого агента, запустите его через LangGraph Studio, а не через GeoView, и задайте `GEOVIEW_RESULT_DIR` вручную:

```bash
export GEOVIEW_RESULT_DIR=/path/to/GeoView/.agent_runtime
langgraph dev --host 127.0.0.1 --port 2024 --no-browser --no-reload --allow-blocking
```

Ключ `--allow-blocking` обязателен: инструменты делают синхронные вызовы, и без него сервер
разработки прерывает запуски. Модуль `graph.py` загружается по пути из `langgraph.json`,
поэтому импорты в нём должны быть абсолютными (`from GeoAgent.configuration import ...`).

## Нужно больше возможностей?

GeoAgent — базовый ИИ-агент для типовых задач.
За расширенными возможностями — например, автоматической генерацией и выполнением кода по
запросу пользователя — обращайтесь к нам за доступом.

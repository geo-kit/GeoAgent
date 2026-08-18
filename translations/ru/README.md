### 🌐 Языки

[English](../../README.md) | **Русский**

# GeoAgent

GeoAgent — это ИИ-помощник, встроенный в [GeoView](https://github.com/geo-kit/GeoView), чтобы ускорить вашу работу.

## Что он умеет

| Инструмент | Что происходит |
|---|---|
| `find_reservoir_models` | Перечисляет подкаталоги и файлы `.DATA` / `.hdf5` в одном каталоге. Содержимое файлов не читает. |
| `load_model_in_geoview` | Открывает модель в GeoView |
| `run_simulation_in_geoview` | Запускает расчёт средствами симулятора JutulDarcy |
| `prepare_optimization_in_geoview` | Запрашивает и заполняет параметры оптимизации NPV и открывает вкладку Optimization |

## Приватность

Агент не запускает оболочку, не исполняет код и не меняет файлы у вас на диске. Он читает
списки файлов в каталоге, но не их содержимое. Всё, что он пишет, попадает в одно место:
каталог артефактов GeoView, в формате JSON.

## Установка

Агента запускает и останавливает сам GeoView, поэтому шаги установки описаны там:
**[Как включить чат](https://github.com/geo-kit/GeoView/blob/main/translations/ru/README.md#как-включить-чат-geoagent)**.

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
| `GEOAGENT_MODEL` | `провайдер:модель`. Провайдеры: `openai`, `lmstudio`, `ollama`. GeoView выставляет её из своих ключей запуска. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI или любая совместимая с ним точка доступа. |
| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | Локальный сервер LM Studio. |
| `OLLAMA_BASE_URL` | Ollama. |
| `GEOVIEW_RESULT_DIR` | Куда доставлять запросы. Выставляется GeoView. |
| `GEOAGENT_MODEL_ROOTS` | Необязательный список разрешённых каталогов, разделитель `os.pathsep`. |

Пример настройки — в файле `.env.example`.

## Как он общается с GeoView

GeoView и агент живут в разных процессах, поэтому передают работу через общий каталог, а
не через API. Агент пишет манифест, затем публикует указатель на него:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json   # что сделать и с чем
<GEOVIEW_RESULT_DIR>/results/latest.json            # {"run_id": ...}, пишется последним
```

GeoView раз в секунду проверяет указатель и направляет манифест по полю `type`. Указатель
агент пишет последним, поэтому GeoView не подхватит наполовину записанный запрос.

У этого агента `type` — всегда запрос: `load_model`, `run_simulation` или
`optimization_setup`. Результаты он не пишет, потому что сам ничего не считает.

Чтобы добавить возможность, заведите новый `type` с обеих сторон; транспорт остаётся
прежним.

## Разработка

Нужны Python 3.13 и [uv](https://docs.astral.sh/uv/). Из этого каталога:

```bash
uv venv && uv pip install -e . --group dev
pytest
ruff check . && ruff format --check .
```

Чтобы дорабатывать самого агента, поднимите его под LangGraph Studio, а не через GeoView. Это
единственный случай, когда `GEOVIEW_RESULT_DIR` задаёте вы: обычно её процессу агента выставляет
GeoView, а здесь — никто, и публикующие инструменты без неё работать откажутся:

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

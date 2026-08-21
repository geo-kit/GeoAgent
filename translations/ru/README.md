### 🌐 Языки

[English](../../README.md) | **Русский**

# GeoAgent

GeoAgent — это встроенный в [GeoView](https://github.com/geo-kit/GeoView) ИИ-помощник, который упрощает рабочие процессы.

## Что он может делать

| Инструмент | Назначение |

|---|---|

| `find_reservoir_models` | Отображает подкаталоги и файлы `.DATA` / `.hdf5` в одном каталоге. Содержимое файлов не читается. |

| `load_model_in_geoview` | Открывает модель в GeoView |

| `run_simulation_in_geoview` | Запускает моделирование с помощью симулятора JutulDarcy |

| `prepare_optimization_in_geoview` | Запрашивает и заполняет параметры оптимизации NPV и открывает вкладку «Оптимизация» |

## Конфиденциальность

Агент не может открыть командную оболочку, выполнить код или изменить файл на вашем диске. Он читает
списки каталогов, а не содержимое колоды. Все, что он записывает, попадает 
в каталог артефактов GeoView, в формате JSON.

## Установка

Требуется Python 3.13, [uv](https://docs.astral.sh/uv/) и [GeoView](https://github.com/geo-kit/GeoView).
Клонируйте репозиторий GeoAgent рядом с GeoView:

```
your-workspace/
├── GeoView/
└── GeoAgent/
```

Затем установите зависимости:

```bash
uv venv && uv pip install -e . --group dev
```

Затем скопируйте `.env.example` в `.env` и заполните ключ API для используемого вами поставщика.

## Запуск

Запустите GeoView с флагом `--agent` (флаги `--agent-provider` и `--agent-model` необязательны):

```bash
python -m geoview.app --agent --agent-provider openai --agent-model gpt-5-mini
```

Чтобы запустить сам агент, используйте LangGraph Studio:

```bash
langgraph dev --host 127.0.0.1 --port 2024 --no-browser
```

Сначала укажите `GEOVIEW_RESULT_DIR` на каталог `.agent_runtime` GeoView. Без него
инструментам некуда будет отправлять запрос, и они вам об этом сообщат.

## Конфигурация

| Переменная | Назначение |

|---|---|

| `GEOAGENT_MODEL` | `provider:model`. Провайдеры: `openai`, `lmstudio`, `ollama`. GeoView устанавливает это из своих собственных флагов. |

| `OPENAI_API_KEY`, `OPENAI_BASE_URL` | OpenAI или  совместимый с OpenAI протокол. |

| `LMSTUDIO_BASE_URL`, `LMSTUDIO_API_KEY`, `LMSTUDIO_MODEL` | Локальный сервер LM Studio. |

| `OLLAMA_BASE_URL` | Ollama. |

| `GEOVIEW_RESULT_DIR` | Куда доставлять запросы. Устанавливается GeoView. |

| `GEOAGENT_MODEL_ROOTS` | Необязательный список разрешенных каталогов, разделенных `os.pathsep`. |

См. `.env.example` для примера конфигурации.

## Как он взаимодействует с GeoView

GeoView и агент являются отдельными процессами и передают работу через общий
каталог, а не через API. Агент записывает команду, а затем публикует указатель на нее:

```
<GEOVIEW_RESULT_DIR>/results/<run_id>/result.json # что делать и с чем
<GEOVIEW_RESULT_DIR>/results/latest.json # {"run_id": ...}, записано последним
```

GeoView проверяет этот указатель раз в секунду и обрабатывает команды.

## Нужны дополнительные функции?

GeoAgent служит базовым агентом ИИ для основных рабочих процессов.
Для доступа к расширенным возможностям, таким как автоматическая генерация и выполнение кода на основе запросов пользователя, пожалуйста, свяжитесь с нами.

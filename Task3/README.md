# Задание 3. Создание векторного индекса базы знаний

## Используемая эмбеддинг-модель

Для построения векторного индекса использована модель bge-base-en, так как она демонстрирует высокое качество семантического поиска и оптимальна для Retrieval-Augmented Generation.

| Параметр          | Значение                                |
| ----------------- | --------------------------------------- |
| Название модели   | BAAI / bge-base-en                      |
| Размер эмбеддинга | 768                                     |
| Язык              | English                                 |
| Ссылка            | https://huggingface.co/BAAI/bge-base-en |

## База знаний

Была использована база знаний по звездным войнам, преобразованная в соответствии с словарем терминов.

## Создание индекса

База знаний была преобразована в векторный индекс с использованием `FAISS`. Документы были разбиты на чанки, для которых с помощью модели `bge-base-en` были сгенерированы эмбеддинги размерности 768. Индекс поддерживает семантический поиск по пользовательским запросам и используется в дальнейшем RAG-пайплайне.

Создание и сохранение индекса осуществляется с помощью скрипта [build_index.py](./build_index.py) 

- количество чанков в индексе - 8033
- время генерации векторов - 737 секунд
- общее время выполнения скрипта - 747 секунд

## Пример запроса к индексу

Для запроса к индексу используется скрипт [search.py](./search.py)

Пример:
```
python3 Task3/search.py 
Введите запрос: Who is Aren Arkan?        

Результаты поиска:

Score: 0.8899
Source: Task2/knowledge_base_final/characters/aren_arkan.md
Text: # Aren Arkan...
--------------------------------------------------------------------------------
Score: 0.8756
Source: Task2/knowledge_base_final/characters/lio_arkan.md
Text: # Lio Arkan...
--------------------------------------------------------------------------------
Score: 0.8738
Source: Task2/knowledge_base_final/characters/xarn_velgor.md
Text: Believed to have been conceived by themidi-chlorians,Aren Arkan wasbornto theslaveShmi Arkan.Although Arkan was listed as being born on thedesertplanetofAridia Primein some sources, confusion existed as to where Arkan was actually born; whereas some records reported his birthplace as Aridia Prime, o...
--------------------------------------------------------------------------------
Score: 0.8738
Source: Task2/knowledge_base_final/characters/aren_arkan.md
Text: Believed to have been conceived by themidi-chlorians,Aren Arkan wasbornto theslaveShmi Arkan.Although Arkan was listed as being born on thedesertplanetofAridia Primein some sources, confusion existed as to where Arkan was actually born; whereas some records reported his birthplace as Aridia Prime, o...
--------------------------------------------------------------------------------
Score: 0.8576
Source: Task2/knowledge_base_final/characters/aren_arkan.md
Text: Sometime later Arkan participated in theBattle of Horain, alongside Kai and Rex. Arkan was contacted by Rex, who was requesting assistance, though he was already preoccupied with a group of Vulture Droids. Arkan later met Kai and Rex in disbelief, noticing they had hijacked an AAT alongside faulty b...
--------------------------------------------------------------------------------
```


import os

from whoosh.index import open_dir, create_in, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser
from whoosh.query import FuzzyTerm
from whoosh.writing import AsyncWriter
from flask import current_app


def create_whoosh_dir(index_dir):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    return index_dir


def add_to_index(index, model):
    def create_schema():
        schema = Schema(
            id=ID(stored=True, unique=True),
            body=TEXT(stored=True)
        )
        return schema

    def create_index():
        if not os.path.exists(full_path):
            schema = create_schema()
            os.makedirs(full_path)
            create_in(full_path, schema=schema)
        elif not exists_in(full_path):
            schema = create_schema()
            create_in(full_path, schema)

    if not current_app.whoosh_dir:
        return

    full_path = os.path.join(current_app.whoosh_dir, index)
    create_index()

    ix = open_dir(full_path)
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)

    with AsyncWriter(ix) as writer:
        writer.update_document(id=str(model.id), **payload)


def remove_from_index(index, obj):
    if not current_app.whoosh_dir:
        return

    current_index_path = os.path.join(current_app.whoosh_dir, index)
    ix = open_dir(current_index_path)

    with AsyncWriter(ix) as writer:
        writer.delete_by_term("id", str(obj.id))


def query_index(obj, query, page, per_page):
    if not current_app.whoosh_dir:
        return [], 0

    current_index_path = os.path.join(current_app.whoosh_dir, obj.__tablename__)
    if not os.path.exists(current_index_path):
        return [], 0

    ix = open_dir(current_index_path)

    with ix.searcher() as searcher:
        query_parser = MultifieldParser(obj.__searchable__, schema=ix.schema, termclass=FuzzyTerm)
        parsed_query = query_parser.parse(query)

        results = searcher.search_page(parsed_query, page, pagelen=per_page)

        ids = [int(hit["id"]) for hit in results]
        total = len(results)

    return ids, total

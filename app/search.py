from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.writing import AsyncWriter
from flask import current_app


def add_to_index(model):
    if not current_app.whoosh_path:
        return

    ix = open_dir(current_app.whoosh_path)
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)

    with AsyncWriter(ix) as writer:
        writer.update_document(id=str(model.id), **payload)


def remove_from_index(model):
    if not current_app.whoosh_path:
        return

    ix = open_dir(current_app.whoosh_path)

    with AsyncWriter(ix) as writer:
        writer.delete_by_term("id", str(model.id))


def query_index(fields, query, page, per_page):
    if not current_app.whoosh_path:
        return [], 0

    ix = open_dir(current_app.whoosh_path)

    with ix.searcher() as searcher:
        query_parser = MultifieldParser(fields, schema=ix.schema)
        parsed_query = query_parser.parse(query)

        results = searcher.search_page(parsed_query, page, pagelen=per_page)
        ids = [int(hit['id']) for hit in results]
        total = len(results)

    return ids, total

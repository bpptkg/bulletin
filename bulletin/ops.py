import sqlalchemy
from sqlalchemy.ext.compiler import compiles


class Upsert(sqlalchemy.sql.expression.Insert):
    """
    MySQL upsert object.

    Source: https://gist.github.com/timtadh/7811458
    """
    pass


@compiles(Upsert, "mysql")
def compile_upsert(insert_stmt, compiler, **kwargs):
    if insert_stmt._has_multi_parameters:
        keys = insert_stmt.parameters[0].keys()
    else:
        keys = insert_stmt.parameters.keys()
    pk = insert_stmt.table.primary_key
    auto = None
    if (len(pk.columns) == 1 and
            isinstance(pk.columns.values()[0].type, sqlalchemy.Integer) and
            pk.columns.values()[0].autoincrement):
        auto = pk.columns.keys()[0]
        if auto in keys:
            keys.remove(auto)
    insert = compiler.visit_insert(insert_stmt, **kwargs)
    ondup = 'ON DUPLICATE KEY UPDATE'
    updates = ', '.join(
        '{} = VALUES({})'.format(c.name, c.name)
        for c in insert_stmt.table.columns
        if c.name in keys
    )
    if auto is not None:
        last_id = '{} = LAST_INSERT_ID({})'.format(auto, auto)
        if updates:
            updates = ', '.join((last_id, updates))
        else:
            updates = last_id
    upsert = ' '.join((insert, ondup, updates))
    return upsert


def mysql_upsert(engine, model, data):
    """
    Insert new data to database model or update the value if primary key exists.
    """
    if not data:
        return

    connection = engine.connect()
    connection.execute(Upsert(model, data))
    connection.close()

from weibonews.db.utils import connect, IncrementalId, ConnectionPool

'''
Manage db connections for modules and locales.

structure:
{
    'module 1': {
        'locale 1': Connection,
        'locale 2': Connection,
    },
    'module 2': {
        'locale 1': Connection,
        'locale 2': Connection,
    },
}
'''
DBS = {}
'''
Manage IncrementalId for modules and locales. Same structure with DBS.
'''
IDS = {}

def select_db(func):
    '''
    Decorator to get db connection of specific locale
    '''
    def select_db_by_locale(*args, **kwargs):
        try:
            locale = args[0]
        except IndexError:
            raise Exception('locale must be the first argument when call %s' % func.__name__)
        try:
            module_name = func.__module__
            db = DBS[module_name][locale]
        except KeyError, err:
            raise Exception('Get db connection for locale %s of module %s failed: %s' % (locale, module_name, err))
        kwargs.update({'db': db})
        return func(*args, **kwargs)
    return select_db_by_locale

def select_ids(func):
    '''
    Decorator to get ids object of specific locale
    '''
    def select_ids_by_locale(*args, **kwargs):
        try:
            locale = args[0]
        except IndexError:
            raise Exception('locale must be the first argument when call %s' % func.__name__)
        try:
            module_name = func.__module__
            ids = IDS[module_name][locale]
        except KeyError, err:
            raise Exception('Get ids for locale %s of module %s failed: %s' % (locale, module_name, err))
        kwargs.update({'ids': ids})
        return func(*args, **kwargs)
    return select_ids_by_locale

def config(module, servers, replset=None):
    assert servers is not None and type(servers) is dict, 'servers must be a dict.'
    name = module.__name__
    DBS[name] = ConnectionPool()
    IDS[name] = ConnectionPool()
    for key, value in servers.items():
        repl = None
        if replset is not None and type(replset) is dict and key in replset:
            repl = replset[key]
        conn = connect(value['server'], port=value['port'], replset=repl)
        # module name and locale as key to manage connections
        DBS[name][key] = conn[value['db']]
        IDS[name][key] = IncrementalId(DBS[name][key])
    # index and save js func
    if hasattr(module, 'INDEXES'):
        ensure_indexes(name, module, module.INDEXES)
    if hasattr(module, 'JS_FUNC'):
        save_js_funcs(name, module, module.JS_FUNC)

def save_js_funcs(name, module, func_table):
    '''
    Save javascript functions to mongodb
    '''
    for name, func_str in func_table.items():
        for key in DBS[name].iterkeys():
            DBS[name][key].system.js.save({"_id" : name, "value" : func_str})

def ensure_index(name, module, collection_name, indexes):
    '''
    Ensure a data access module's collection indexes.
    '''
    for key in DBS[name].iterkeys():
        collection = DBS[name][key][collection_name]
        for index in indexes:
            collection.ensure_index(index)

def ensure_indexes(name, module, index_table):
    '''
    Ensure a data access module's indexes.
    '''
    for collection, indexes in index_table.items():
        ensure_index(name, module, collection, indexes)

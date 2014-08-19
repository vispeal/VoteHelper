'''
Created on: Mar 05, 2014

@author: qwang
'''

_MARK_ENTITY_FORMAT = '<a data-entity="%s">%s</a>'

ENTITY_TYPE = {
    'publication': 8,
}

_PUBLICATION_LEFT_SYMBOLS = [u"\u300a", u"\u3010", u"\u201c"]
_PUBLICATION_RIGHT_SYMBOLS = [u"\u300b", u"\u3011", u"\u201d"]

def rreplace(s, old, new, occurrence):
    '''
    Replace old substring with new substring in string s in reverse order, just
    replace the first N occurrence.
    '''
    li = s.rsplit(old, occurrence)
    return new.join(li)

def _decode(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return s

def _contain_publication_symbol(index, entity, string):
    '''
    Check if entity at index in string contains publication symbol
    '''
    if index < 1 or index + len(entity) + 1> len(string):
        # index out of bound
        return False
    left = string[index-1]
    right = string[index+len(entity)]
    return left in _PUBLICATION_LEFT_SYMBOLS and right in _PUBLICATION_RIGHT_SYMBOLS

def _find_publication_entity(entity, string):
    '''
    Find first and last occurrence of publication entity, return index of occurrence.
    If not in string, return -1
    '''
    first_index = -1
    last_index = -1
    # find index of first occurrence
    temp_str = string
    while True:
        index = temp_str.find(entity)
        if index == -1:
            first_index = -1
            break
        if _contain_publication_symbol(index, entity, temp_str):
            first_index = index
            break
        else:
            temp_str = temp_str[index+len(entity):]
    if first_index == -1:
        # can not find
        return -1, -1
    # find index of last occurrence
    temp_str = string
    while True:
        index = temp_str.rfind(entity)
        if index == -1 or index == first_index:
            last_index = -1
            break
        if _contain_publication_symbol(index, entity, temp_str):
            last_index = index
            break
        else:
            temp_str = temp_str[:index]
    return first_index, last_index

def is_in_title(entity, entity_type, title):
    '''
    Check if the entity of specific category is in title
    '''
    entity = _decode(entity)
    title = _decode(title)
    # entity in lower case, so change title to lower case
    temp_title = title.lower()
    # add logic to handle category publication
    if entity_type == ENTITY_TYPE['publication']:
        index, _ = _find_publication_entity(entity, temp_title)
        return index != -1
    return temp_title.find(entity) != -1

def _mark_publication_entity(entity, content):
    # mark publication entity
    lower_content = content.lower()
    first_index, last_index = _find_publication_entity(entity, lower_content)
    if first_index == -1:
        # not found
        return content
    # mark first occurrence
    first_entity = content[first_index-1:first_index+len(entity)+1]
    if last_index != -1:
        last_entity = content[last_index-1:last_index+len(entity)+1]
    content = content.replace(first_entity, _MARK_ENTITY_FORMAT % (entity, first_entity), 1)
    if last_index != -1:
        # mark last occurrence
        content = rreplace(content, last_entity, _MARK_ENTITY_FORMAT % (entity, last_entity), 1)
    return content

def mark_entity(content, entity, entity_type):
    '''
    Mark entity in content, just mark the first and last appearance

    NOTICE this method can not be called more than once for the same entity and content.
    '''
    content = _decode(content)
    entity = _decode(entity)
    if entity_type == ENTITY_TYPE['publication']:
        return _mark_publication_entity(entity, content)
    # handle lowser case situation
    temp_content = content.lower()
    first_index = temp_content.find(entity)
    last_index = temp_content.rfind(entity)
    if first_index == -1:
        # not found entity in content
        return content
    first_entity = content[first_index:first_index+len(entity)]
    if first_index != last_index:
        last_entity = content[last_index:last_index+len(entity)]
    content = content.replace(first_entity, _MARK_ENTITY_FORMAT % (entity, first_entity), 1)
    if first_index != last_index:
        content = rreplace(content, last_entity, _MARK_ENTITY_FORMAT % (entity, last_entity), 1)
    return content

import json
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import List, Tuple

# 设置 Google Knowledge Graph API 的基本调用函数
def query_knowledge_graph(api_key, query, limit=10):
    """使用 Google Knowledge Graph API 进行查询"""
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': limit,
        'indent': True,
        'key': api_key,
    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    return response


def get_label_with_api(api_key, entity: str) -> str:
    """通过 Google Knowledge Graph API 获取实体的标签"""
    response = query_knowledge_graph(api_key, query=entity)
    for element in response.get('itemListElement', []):
        result = element.get('result', {})
        if result.get('@id') == entity:
            return result.get('name')
    return None


def get_in_relations_with_api(api_key, entity: str) -> List[str]:
    """通过 Google Knowledge Graph API 获取实体的入关系"""
    response = query_knowledge_graph(api_key, query=entity)
    in_relations = set()
    for element in response.get('itemListElement', []):
        result = element.get('result', {})
        if 'detailedDescription' in result:
            in_relations.add(result['detailedDescription'].get('articleBody', ''))
    return list(in_relations)


def get_out_relations_with_api(api_key, entity: str) -> List[str]:
    """通过 Google Knowledge Graph API 获取实体的出关系"""
    response = query_knowledge_graph(api_key, query=entity)
    out_relations = set()
    for element in response.get('itemListElement', []):
        result = element.get('result', {})
        if 'detailedDescription' in result:
            out_relations.add(result['detailedDescription'].get('articleBody', ''))
    return list(out_relations)


def get_1hop_relations_with_api(api_key, entity: str) -> List[str]:
    """通过 Google Knowledge Graph API 获取实体的 1-hop 关系"""
    in_relations = get_in_relations_with_api(api_key, entity)
    out_relations = get_out_relations_with_api(api_key, entity)
    return list(set(in_relations + out_relations))


def get_2hop_relations_with_api(api_key, entity: str) -> Tuple[List[str], List[str]]:
    """通过 Google Knowledge Graph API 获取实体的 2-hop 关系"""
    one_hop_relations = get_1hop_relations_with_api(api_key, entity)
    two_hop_relations = set()
    for relation in one_hop_relations:
        two_hop_relations.update(get_1hop_relations_with_api(api_key, relation))
    return one_hop_relations, list(two_hop_relations)


def get_entity_labels(api_key, entities: List[str]) -> dict:
    """获取多个实体的标签"""
    res = {}
    for entity in entities:
        res[entity] = get_label_with_api(api_key, entity)
    return res


def execute_query_with_api(api_key, query: str):
    """通过 Google Knowledge Graph API 执行查询（仅支持实体查询，SPARQL 查询需重新设计）"""
    raise NotImplementedError("Knowledge Graph API 不支持直接 SPARQL 查询，请重新设计查询逻辑")


def get_freebase_mid_from_wikiID(api_key, wikiID: int) -> str:
    """通过 Google Knowledge Graph API 获取 Freebase MID"""
    response = query_knowledge_graph(api_key, query=str(wikiID))
    for element in response.get('itemListElement', []):
        result = element.get('result', {})
        if result.get('@id'):
            return result['@id']
    return ''


def dump_json(obj, fname, indent=4, mode='w', encoding="utf8", ensure_ascii=False):
    """保存为 JSON 文件"""
    with open(fname, mode, encoding=encoding) as f:
        json.dump(obj, f, indent=indent, ensure_ascii=ensure_ascii)


def load_json(fname, mode="r", encoding="utf8"):
    """加载 JSON 文件"""
    with open(fname, mode, encoding=encoding) as f:
        return json.load(f)


if __name__ == '__main__':
    api_key = "AIzaSyAt3kOcaCVjGNGWViqx91yihvuxvN9Nq9g"  

    # 示例调用
    print("获取实体标签:")
    print(get_label_with_api(api_key, 'Taylor Swift'))

    print("\n获取入关系:")
    print(get_in_relations_with_api(api_key, 'Taylor Swift'))

    print("\n获取出关系:")
    print(get_out_relations_with_api(api_key, 'Taylor Swift'))

    print("\n获取 1-hop 关系:")
    print(get_1hop_relations_with_api(api_key, 'Taylor Swift'))

    print("\n获取 2-hop 关系:")
    one_hop, two_hop = get_2hop_relations_with_api(api_key, 'Taylor Swift')
    print("1-hop:", one_hop)
    print("2-hop:", two_hop)

    print("\n通过 Wikipedia ID 获取 Freebase MID:")
    print(get_freebase_mid_from_wikiID(api_key, 39027))

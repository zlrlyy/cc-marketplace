#!/usr/bin/env python3
"""
XMind 用例解析工具（旧格式，基于 content.xml）

用法：
    from lib.parse_xmind import parse_xmind

    cases = parse_xmind('reports/test-cases.xmind')
    # 返回结构化用例列表，每个元素格式：
    # {
    #   "id": "TC001",
    #   "title": "用例名称",
    #   "module": "一、模块名称",
    #   "preconditions": ["前置条件1"],
    #   "steps": ["操作步骤1"],
    #   "expected": ["预期结果1"],
    #   "path": "根节点 > 模块 > TC001"
    # }

命令行用法：
    python3 lib/parse_xmind.py reports/test-cases.xmind
"""
import zipfile
import re
import json
import sys
import xml.etree.ElementTree as ET

NS = 'urn:xmind:xmap:xmlns:content:2.0'

MARKER_PRECONDITION = 'symbol-right'   # 前置条件
MARKER_STEP = 'symbol-question'        # 操作步骤
MARKER_TC = 'symbol-plus'              # 测试用例标识


def _get_title(element):
    title_el = element.find(f'{{{NS}}}title')
    return title_el.text.strip() if title_el is not None and title_el.text else ''


def _get_markers(element):
    marker_refs = element.findall(f'.//{{{NS}}}marker-ref')
    return {m.get('marker-id', '') for m in marker_refs}


def _get_child_topics(element):
    children_el = element.find(f'{{{NS}}}children')
    if children_el is None:
        return []
    topics_el = children_el.find(f'{{{NS}}}topics')
    return list(topics_el) if topics_el is not None else list(children_el)


def _is_tc_node(element):
    title = _get_title(element)
    markers = _get_markers(element)
    return MARKER_TC in markers or bool(re.match(r'TC\d+', title))


def _parse_tc(element, module, root_title):
    title = _get_title(element)
    tc_id = re.match(r'(TC\d+)', title)
    tc_id = tc_id.group(1) if tc_id else ''

    preconditions, steps, expected = [], [], []
    for child in _get_child_topics(element):
        child_title = _get_title(child)
        if not child_title:
            continue
        markers = _get_markers(child)
        if MARKER_PRECONDITION in markers:
            preconditions.append(child_title)
        elif MARKER_STEP in markers:
            steps.append(child_title)
        else:
            expected.append(child_title)

    return {
        'id': tc_id,
        'title': title,
        'module': module,
        'preconditions': preconditions,
        'steps': steps,
        'expected': expected,
        'path': f'{root_title} > {module} > {title}',
    }


def _extract_flat_paths(element, path):
    """回退模式：无 TC 标记时，返回所有叶节点路径"""
    results = []
    title = _get_title(element)
    children = _get_child_topics(element)
    if not children:
        if title and path:
            results.append(' > '.join(path + [title]))
        return results
    new_path = path + [title] if title else path
    for child in children:
        results.extend(_extract_flat_paths(child, new_path))
    return results


def _load_xml(xmind_path):
    with zipfile.ZipFile(xmind_path) as z:
        with z.open('content.xml') as f:
            raw = f.read().decode('utf-8', errors='replace')

    # 转义 title 内容中未转义的 < > 字符
    def _escape_title(m):
        inner = m.group(1)
        inner = inner.replace('&', '&amp;')
        inner = re.sub(r'<(?!/)', '&lt;', inner)
        inner = inner.replace('>', '&gt;')
        return f'<title>{inner}</title>'

    fixed = re.sub(r'<title>(.*?)</title>', _escape_title, raw, flags=re.DOTALL)
    return ET.fromstring(fixed)


def parse_xmind(xmind_path):
    """
    解析 XMind 文件，返回结构化用例列表。

    如果节点有 symbol-plus 标记或标题以 TCxxx 开头，则按结构化用例解析；
    否则回退为扁平路径列表（每条路径作为一个 step 的用例）。
    """
    root = _load_xml(xmind_path)
    sheets = root.findall(f'{{{NS}}}sheet')
    cases = []

    for sheet in sheets:
        root_topic = sheet.find(f'{{{NS}}}topic')
        if root_topic is None:
            continue
        root_title = _get_title(root_topic)

        # 遍历模块层
        for module_el in _get_child_topics(root_topic):
            module_title = _get_title(module_el)
            tc_nodes = _get_child_topics(module_el)

            if tc_nodes and _is_tc_node(tc_nodes[0]):
                # 结构化模式
                for tc_el in tc_nodes:
                    cases.append(_parse_tc(tc_el, module_title, root_title))
            else:
                # 回退为扁平路径
                paths = _extract_flat_paths(module_el, [root_title])
                for p in paths:
                    cases.append({
                        'id': '',
                        'title': p,
                        'module': module_title,
                        'preconditions': [],
                        'steps': [p],
                        'expected': [],
                        'path': p,
                    })

    return cases


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'reports/test-cases.xmind'
    cases = parse_xmind(path)
    print(json.dumps(cases, ensure_ascii=False, indent=2))
    print(f'\n# Total: {len(cases)} cases', file=sys.stderr)

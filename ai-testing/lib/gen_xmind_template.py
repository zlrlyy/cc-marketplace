#!/usr/bin/env python3
"""
XMind 测试用例生成模板
使用方法：复制此模板，修改 DATA 部分的内容，运行即可生成 .xmind 文件
"""
import random
import string
import zipfile
import os
import time


def gen_id():
    """生成 XMind 风格的随机 ID（25位小写字母+数字）"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(25))


TS = str(int(time.time() * 1000))
M = 'modified-by="admin"'


def topic(title, marker_ids=None, children=None, width=False):
    """
    构建一个 topic XML 字符串

    参数:
        title: 节点标题
        marker_ids: 标记列表，如 ['symbol-plus', 'priority-1']
            - symbol-plus: 测试用例标识
            - priority-1/2/3: 优先级
            - symbol-right: 前置条件（勾号）
            - symbol-question: 操作步骤（问号）
            - 无标记: 预期结果
        children: 子节点列表（每个元素是 topic() 的返回值）
        width: 是否添加 svg:width="500"（长标题时使用）
    """
    tid = gen_id()
    w = ' svg:width="500"' if width else ''
    markers = ''
    if marker_ids:
        refs = ''.join(f'<marker-ref marker-id="{m}"/>' for m in marker_ids)
        markers = f'<marker-refs>{refs}</marker-refs>'
    kids = ''
    if children:
        inner = ''.join(children)
        kids = f'<children><topics type="attached">{inner}</topics></children>'
    return f'<topic id="{tid}" {M} timestamp="{TS}"><title{w}>{title}</title>{markers}{kids}</topic>'


def build_xmind(root_title, modules, output_path):
    """
    生成 xmind 文件

    参数:
        root_title: 根节点标题（如 "XX功能测试用例"）
        modules: 模块列表，每个元素是 topic() 的返回值
        output_path: 输出文件路径
    """
    sheet_id = gen_id()
    theme_id = gen_id()
    root_id = gen_id()
    module_count = len(modules)

    all_modules = ''.join(modules)

    root_topic = (
        f'<topic id="{root_id}" {M} structure-class="org.xmind.ui.map.unbalanced" timestamp="{TS}">'
        f'<title>{root_title}</title>'
        f'<children><topics type="attached">{all_modules}</topics></children>'
        f'<extensions><extension provider="org.xmind.ui.map.unbalanced">'
        f'<content><right-number>{module_count}</right-number></content>'
        f'</extension></extensions>'
        f'</topic>'
    )

    content_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" '
        'xmlns:fo="http://www.w3.org/1999/XSL/Format" '
        'xmlns:svg="http://www.w3.org/2000/svg" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'{M} timestamp="{TS}" version="2.0">'
        f'<sheet id="{sheet_id}" {M} theme="{theme_id}" timestamp="{TS}">'
        f'{root_topic}'
        f'<title>画布 1</title>'
        f'</sheet>'
        f'</xmap-content>'
    )

    # "专业"主题样式
    sty = [gen_id() for _ in range(10)]
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" '
        'xmlns:fo="http://www.w3.org/1999/XSL/Format" '
        'xmlns:svg="http://www.w3.org/2000/svg" version="2.0">'
        '<automatic-styles>'
        f'<style id="{sty[0]}" name="" type="topic"><topic-properties border-line-color="#558ED5" border-line-width="3pt" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt"/></style>'
        f'<style id="{sty[1]}" name="" type="summary"><summary-properties line-color="#C3D69B" line-width="5pt" shape-class="org.xmind.summaryShape.square"/></style>'
        f'<style id="{sty[2]}" name="" type="boundary"><boundary-properties fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" line-color="#77933C" line-pattern="dot" line-width="3pt" shape-class="org.xmind.boundaryShape.roundedRect" svg:fill="#C3D69B" svg:opacity=".2"/></style>'
        f'<style id="{sty[3]}" name="" type="topic"><topic-properties border-line-color="#F1BD51" border-line-width="2pt" fo:font-family="Microsoft YaHei" svg:fill="#FBF09C"/></style>'
        f'<style id="{sty[4]}" name="" type="topic"><topic-properties border-line-color="#558ED5" border-line-width="5pt" fo:color="#376092" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#DCE6F2"/></style>'
        f'<style id="{sty[5]}" name="" type="topic"><topic-properties border-line-color="#558ED5" border-line-width="2pt" fo:color="#17375E" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#DCE6F2"/></style>'
        f'<style id="{sty[6]}" name="" type="topic"><topic-properties border-line-width="0pt" fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" line-class="org.xmind.branchConnection.curve" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#77933C"/></style>'
        f'<style id="{sty[7]}" name="" type="topic"><topic-properties border-line-width="0pt" fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-weight="bold" line-color="#558ED5" svg:fill="#558ED5"/></style>'
        f'<style id="{sty[8]}" name="" type="relationship"><relationship-properties arrow-end-class="org.xmind.arrowShape.triangle" fo:color="#595959" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" fo:font-weight="normal" fo:text-decoration="none" line-color="#77933C" line-pattern="dash" line-width="3pt"/></style>'
        f'<style id="{sty[9]}" name="" type="map"><map-properties color-gradient="none" line-tapered="none" multi-line-colors="none" svg:fill="#FFFFFF"/></style>'
        '</automatic-styles>'
        '<master-styles>'
        f'<style id="{theme_id}" name="专业" type="theme"><theme-properties>'
        f'<default-style style-family="subTopic" style-id="{sty[0]}"/>'
        f'<default-style style-family="summary" style-id="{sty[1]}"/>'
        f'<default-style style-family="boundary" style-id="{sty[2]}"/>'
        f'<default-style style-family="calloutTopic" style-id="{sty[3]}"/>'
        f'<default-style style-family="centralTopic" style-id="{sty[4]}"/>'
        f'<default-style style-family="mainTopic" style-id="{sty[5]}"/>'
        f'<default-style style-family="summaryTopic" style-id="{sty[6]}"/>'
        f'<default-style style-family="floatingTopic" style-id="{sty[7]}"/>'
        f'<default-style style-family="relationship" style-id="{sty[8]}"/>'
        f'<default-style style-family="map" style-id="{sty[9]}"/>'
        '</theme-properties></style>'
        '</master-styles>'
        '</xmap-styles>'
    )

    meta_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">'
        f'<Author><Name>admin</Name></Author>'
        f'<Create><Time>{TS}</Time></Create>'
        '</meta>'
    )

    manifest_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" password-hint="">'
        '<file-entry full-path="content.xml" media-type="text/xml"/>'
        '<file-entry full-path="META-INF/" media-type=""/>'
        '<file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>'
        '<file-entry full-path="meta.xml" media-type="text/xml"/>'
        '<file-entry full-path="styles.xml" media-type="text/xml"/>'
        '</manifest>'
    )

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('content.xml', content_xml)
        zf.writestr('styles.xml', styles_xml)
        zf.writestr('meta.xml', meta_xml)
        zf.writestr('META-INF/manifest.xml', manifest_xml)

    print(f'Generated: {output_path}')
    print(f'File size: {os.path.getsize(output_path)} bytes')


# ============================================================
# DATA - 修改以下内容来生成不同的测试用例
# ============================================================
if __name__ == '__main__':
    # 示例：微信更换头像功能测试用例

    # TC001
    tc001 = topic('TC001-示例用例名称', ['symbol-plus', 'priority-1'], [
        topic('前置条件描述', ['symbol-right']),
        topic('操作步骤1', ['symbol-question']),
        topic('操作步骤2', ['symbol-question']),
        topic('预期结果描述'),
    ])

    # 模块
    mod1 = topic('一、模块名称', children=[tc001])

    # 生成文件
    build_xmind(
        root_title='XX功能测试用例',
        modules=[mod1],
        output_path='output.xmind'
    )

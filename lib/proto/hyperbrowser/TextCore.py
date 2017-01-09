from proto.hyperbrowser.HtmlCore import HtmlCore as HbHtmlCore
from proto.TextCore import TextCore as ProtoTextCore


class TextCore(ProtoTextCore):
    HTML_CORE_CLS = HbHtmlCore

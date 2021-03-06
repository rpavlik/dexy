from dexy.dexy_filter import DexyFilter
from ordereddict import OrderedDict
from pygments import highlight
from pygments.formatters import get_formatter_for_filename
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.agile import PythonConsoleLexer
from pygments.lexers.agile import RubyConsoleLexer
from pygments.lexers.special import TextLexer
from pygments.lexers.web import JavascriptLexer
from pygments.lexers.web import XmlLexer

class PygFilter(DexyFilter):
    """
    Apply Pygments syntax highlighting.
    """
    INPUT_EXTENSIONS = [".*"]
    IMAGE_OUTPUT_EXTENSIONS = ['.png', '.bmp', '.gif', '.jpg']
    MARKUP_OUTPUT_EXTENSIONS = [".html", ".tex", ".svg"]
    OUTPUT_EXTENSIONS = MARKUP_OUTPUT_EXTENSIONS + IMAGE_OUTPUT_EXTENSIONS
    ALIASES = ['pyg', 'pygments']
    FINAL = False

    def process_dict(self, input_dict):
        ext = self.artifact.input_ext

        ### @export "custom-file-extension-handling"
        if ext == '.pycon':
            lexer = PythonConsoleLexer()
        elif ext == '.rbcon':
            lexer = RubyConsoleLexer()
        elif ext in ('.json', '.dexy'):
            lexer = JavascriptLexer()
        elif ext == '.Rd':
            lexer = TextLexer()
        elif ext == '.svg':
            lexer = XmlLexer()
        else:
            fake_file_name = "input_text%s" % ext
            lexer = get_lexer_for_filename(fake_file_name)

        ### @export "pygments-args"
        if self.artifact.args.has_key('pygments'):
            pygments_args = self.artifact.args['pygments']
        else:
            pygments_args = {}

        formatter_args = {'lineanchors' : self.artifact.document_key }
        # for now we assume all pygments args are for the formatter...
        formatter_args.update(pygments_args)

        formatter = get_formatter_for_filename(self.artifact.filename(),
                **formatter_args)
        ### @end
        # TODO whitelist acceptable formatter args
        # TODO allow passing lexer args?

        if self.artifact.ext in self.IMAGE_OUTPUT_EXTENSIONS:
            self.artifact.binary_output = True
            f = open(self.artifact.filepath(), 'w')
            f.write(highlight(self.artifact.input_text(), lexer, formatter))
            f.close()
        else:
            output_dict = OrderedDict()
            for k, v in input_dict.items():
                # TODO figure out where these characters are coming from and don't hard-code this.
                v = str(v.replace(" \x08", "").replace(chr(13), ""))
                try:
                    output_dict[k] = str(highlight(v, lexer, formatter))
                except UnicodeEncodeError as e:
                    self.artifact.log.warn("error processing section %s of file %s" % (k, self.artifact.key))
                    raise e
            return output_dict

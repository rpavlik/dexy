from dexy.artifacts.file_system_json_artifact import FileSystemJsonArtifact
from dexy.controller import Controller
from dexy.document import Document
from dexy.tests.utils import tempdir
from dexy.constants import NullHandler
from modargs import args as modargs
import dexy.commands
import dexy.database
import dexy.filters.python_filters
import os

SIMPLE_PY_CONFIG = {
   "." : {
       "@simple.py|py" : {
           "contents" : "x=6\\ny=7\\nprint x*y"
        }
    }
}

def test_init():
    c = Controller()
    assert isinstance(c.args, dict)
    assert isinstance(c.config, dict)
    assert len(c.args) == 0
    assert len(c.config) == 0

    assert len(c.log.handlers) == 1
    # Because we didn't pass a logfile or logsdir...
    assert isinstance(c.log.handlers[0], NullHandler)

    assert len(c.reports_dirs) > 1
    assert len(c.artifact_classes) > 0

def test_init_with_artifact_class():
    args = { "artifactclass" : "FileSystemJsonArtifact" }
    c = Controller(args)
    assert c.artifact_class == FileSystemJsonArtifact

def test_init_with_db():
    args = { "dbclass" : "CsvDatabase", "dbfile" : "db.csv", "logsdir" : "logs" }
    c = Controller(args)
    assert isinstance(c.db, dexy.database.Database)

def test_run():
    with tempdir():
        fn = modargs.function_for(dexy.commands, "dexy")
        args = modargs.determine_kwargs(fn)
        args['globals'] = []
        os.mkdir(args['logsdir'])
        c = Controller(args)
        c.config = SIMPLE_PY_CONFIG
        c.process_config()
        assert c.members.has_key("simple.py|py")
        assert isinstance(c.members["simple.py|py"], Document)
        assert sorted(c.batch_info().keys()) == ["args", "config", "docs"]

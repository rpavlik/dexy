from dexy.commands import *
from dexy.constants import Constants
from dexy.tests.utils import divert_stdout
from dexy.tests.utils import tempdir
import csv
import dexy.artifact
import dexy.utils
import os

SIMPLE_PY_CONFIG = """
{
   "@simple.py|py" : {
       "contents" : "x=6\\ny=7\\nprint x*y"
    }
}"""

def test_setup_message_without_config():
    with tempdir():
        with divert_stdout() as stdout:
            setup_command()
            assert "You are almost ready" in stdout.getvalue()

def test_setup_message_with_config():
    with tempdir():
        with divert_stdout() as stdout:
            with open(Constants.DEFAULT_CONFIG, "w") as f:
                f.write(SIMPLE_PY_CONFIG)
            setup_command()
            assert "You are now ready" in stdout.getvalue()

def test_commands_reset():
    with tempdir():
        setup_command()
        reset_command()
        assert check_setup()

def test_commands_reset_custom_location():
    with tempdir():
        logsdir = "logsx"
        artifactsdir = "artifactsx"
        setup_command(logsdir=logsdir, artifactsdir=artifactsdir)
        assert check_setup(logsdir=logsdir, artifactsdir=artifactsdir)
        assert os.path.exists(artifactsdir)
        assert os.path.exists(logsdir)
        reset_command(logsdir=logsdir, artifactsdir=artifactsdir)
        assert check_setup(logsdir=logsdir, artifactsdir=artifactsdir)

def test_commands_setup_cleanup():
    with tempdir():
        with divert_stdout() as stdout:
            setup_command()
            assert "You are almost ready" in stdout.getvalue()
            assert os.path.exists(Constants.DEFAULT_ADIR)
            assert os.path.exists(Constants.DEFAULT_LDIR)
            assert check_setup()

        cleanup_command()
        assert not os.path.exists(Constants.DEFAULT_ADIR)
        assert not os.path.exists(Constants.DEFAULT_LDIR)
        assert not check_setup()

def test_commands_dexy_without_setup():
    with tempdir():
        with divert_stdout() as stdout:
            try:
                dexy_command()
                assertFalse # should not get here
            except SystemExit as e:
                assert "Please run 'dexy setup'" in stdout.getvalue()
                assert not check_setup()
                assert e.code == 1

def test_commands_filters():
    with divert_stdout() as stdout:
        filters_command()
        assert "cp : CopyFilter" in stdout.getvalue()

def test_commands_reporters():
    with divert_stdout() as stdout:
        reporters_command()
        assert "OutputReporter" in stdout.getvalue()

def test_help_text():
    assert "Available commands for dexy are" in help_text()
    assert "e.g. 'dexy setup --artifactsdir artifacts'" in help_text("setup")
    assert "e.g. 'dexy --artifactsdir artifacts'" in help_text("dexy")

def test_help_command():
    with divert_stdout() as stdout:
        help_command()
        assert stdout.getvalue() == help_text()

def test_help_command_with_on():
    with divert_stdout() as stdout:
        help_command("setup")
        assert stdout.getvalue() == help_text("setup")

def test_dexy_command():
    with tempdir():
        setup_command()
        dexy_command()

def test_dexy_command_with_data():
    with tempdir():
        with open(".dexy", "w") as f:
            f.write(SIMPLE_PY_CONFIG)

        setup_command()
        dexy_command(danger=True)

        assert os.path.exists("logs/db.csv"), "database file should be created"
        assert os.path.exists("logs/batch-00001.json")

        with open("logs/db.csv", "rb") as f:
            reader = csv.DictReader(f)
            # check that all files listed in the db have been created
            for row in reader:
                h = row['hashstring']
                assert os.path.exists("artifacts/%s-output.json" % h)
                assert os.path.exists("artifacts/%s-meta.json" % h)

        # Test database.
        reporter = dexy.reporter.Reporter()
        reporter.load_batch_artifacts()
        for a in reporter.artifacts.values():
            assert isinstance(a, dexy.artifact.Artifact)


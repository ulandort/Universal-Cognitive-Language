"""Compatibility import for canonical UCL/2.0 SAP-1 schema in src/.

Benchmark code historically imports this module by filename; the authoring
rules are now maintained only in src/structural_authoring.py.
"""
import importlib.util
from pathlib import Path
_source=Path(__file__).resolve().parents[1]/'src'/'structural_authoring.py'
_spec=importlib.util.spec_from_file_location('_ucl2_authoring_schema',_source)
_schema=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_schema)
for _name in dir(_schema):
    if not _name.startswith('__'):
        globals()[_name]=getattr(_schema,_name)
def __getattr__(name):
    return getattr(_schema,name)

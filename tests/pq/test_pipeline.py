import pytest

import psycopg3
from psycopg3 import pq


def test_work_in_progress(pgconn):
    assert not pgconn.nonblocking
    with pytest.raises(
        psycopg3.OperationalError,
        match="cannot exit pipeline mode with uncollected results",
    ):
        with pgconn.pipeline_mode():
            pgconn.send_query_params(b"select $1", [b"1"])


def test_simple(pgconn):
    # Adapted from src/test/modules/libpq_pipeline/libpq_pipeline.c::test_simple_pipeline()
    assert not pgconn.nonblocking
    with pgconn.pipeline_mode():
        pgconn.send_query_params(b"select $1", [b"1"])
        pgconn.pipeline_sync()
        result1 = pgconn.get_result()
        assert result1 is not None
        assert result1.status == pq.ExecStatus.TUPLES_OK
        assert pgconn.get_result() is None
        result2 = pgconn.get_result()
        assert result2 is not None
        assert result2.status == pq.ExecStatus.PIPELINE_SYNC
        assert pgconn.get_result() is None
        assert pgconn.pipeline_status() == pq.PipelineStatus.ON
    assert pgconn.pipeline_status() == pq.PipelineStatus.OFF
    assert result1.get_value(0, 0) == b"1"


def test_multi_pipelines(pgconn):
    # Adapted from src/test/modules/libpq_pipeline/libpq_pipeline.c::test_multi_pipelines()
    pass

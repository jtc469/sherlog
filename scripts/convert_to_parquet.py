import os
import time
from pathlib import Path

import duckdb

RAW = Path("data/raw")
OUT = Path("data/parquet")
TMP = f"/tmp/{os.environ.get('USER', 'user')}_duckdb"

SCHEMAS = {
    "redteam": {
        "time": "BIGINT", "user": "VARCHAR",
        "src_comp": "VARCHAR", "dst_comp": "VARCHAR",
    },
    "dns": {
        "time": "BIGINT", "src_comp": "VARCHAR", "resolved_comp": "VARCHAR",
    },
    "flows": {
        "time": "BIGINT", "duration": "BIGINT",
        "src_comp": "VARCHAR", "src_port": "VARCHAR",
        "dst_comp": "VARCHAR", "dst_port": "VARCHAR",
        "protocol": "INTEGER", "packets": "BIGINT", "bytes": "BIGINT",
    },
    "proc": {
        "time": "BIGINT", "user": "VARCHAR", "comp": "VARCHAR",
        "process": "VARCHAR", "event": "VARCHAR",
    },
    "auth": {
        "time": "BIGINT", "src_user": "VARCHAR", "dst_user": "VARCHAR",
        "src_comp": "VARCHAR", "dst_comp": "VARCHAR",
        "auth_type": "VARCHAR", "logon_type": "VARCHAR",
        "orientation": "VARCHAR", "outcome": "VARCHAR",
    },
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    Path(TMP).mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.sql("SET threads = 16")
    con.sql("SET memory_limit = '32GB'")
    con.sql(f"SET temp_directory = '{TMP}'")
    con.sql("SET preserve_insertion_order = false")

    for name, cols in SCHEMAS.items():
        src, dst = RAW / f"{name}.txt.gz", OUT / f"{name}.parquet"
        if dst.exists():
            print(f"{name}: already converted, skipping")
            continue
        col_sql = "{" + ", ".join(f"'{c}': '{t}'" for c, t in cols.items()) + "}"
        t0 = time.time()
        con.sql(f"""
            COPY (
                SELECT * FROM read_csv('{src}', header=false, delim=',',
                                       nullstr='?', columns={col_sql})
            ) TO '{dst}' (FORMAT parquet, COMPRESSION zstd, ROW_GROUP_SIZE 1000000)
        """)
        n = con.sql(f"SELECT count(*) FROM '{dst}'").fetchone()[0]
        print(f"{name}: {n:,} rows in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
/*

*/


CREATE TABLE IF NOT EXISTS TEST (
    TAB_TYPE          INTEGER,
    TAB_MAX_INDEX     INTEGER DEFAULT 5
);

INSERT INTO TEST (TAB_TYPE) VALUES(NULL);

PRAGMA user_version = 1;

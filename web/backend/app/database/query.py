from sqlalchemy import text

INSERT_FILE_META_DATA = text(
    """
INSERT INTO files (id, user_id, file_name, file_path, created_at) VALUES 
(
    :file_id, 
    :user_id,
    :file_name,
    :file_path,
    current_timestamp)
    """
)

SELECT_USERS = text(
    """
SELECT id, *
FROM users
    """
)

SELECT_FILES = text(
    """
SELECT *
FROM files f
WHERE f.user_id = :user_id
"""
)


INSERT_STT_RESULT_DATA = text(
    """
INSERT INTO stt_results (file_id, index, start_time, end_time, text, confidence, speaker_label, text_edited, created_at) VALUES 
(
    :file_id, 
    :index,
    :start_time,
    :end_time,
    :text,
    :confidence,
    :speaker_label,
    :text_edited,
    current_timestamp)
    """
)

SELECT_STT_RESULTS = text(
    """
SELECT *
FROM stt_results sr
WHERE sr.file_id = :file_id
ORDER BY sr.index asc
    """
)

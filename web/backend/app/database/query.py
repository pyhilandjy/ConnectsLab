from sqlalchemy import text

INSERT_AUDIO_FILE_META_DATA = text(
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

INSERT_IMAGE_FILE_META_DATA = text(
    """
INSERT INTO image_file (id, speaker, user_id, start_date, end_date, image_path, type) VALUES 
(
    :image_id, 
    :speaker,
    :user_id,
    :start_date,
    :end_date,
    :image_path,
    :type)
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


SELECT_STT_RESULTS_WORDCLOUD = text(
    """
    SELECT sr.*
    FROM stt_results sr
    JOIN files f ON sr.file_id = f.id
    WHERE f.user_id = :user_id
        AND sr.created_at BETWEEN :start_date AND :end_date
    ORDER BY sr.created_at ASC, sr.index ASC
    """
)

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

INSERT_IMAGE_FILES_META_DATA = text(
    """
INSERT INTO image_files (id, speaker, user_id, start_date, end_date, image_path, type) VALUES 
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


SELECT_STT_RESULTS_FOR_IMAGE = text(
    """
    SELECT sr.*
    FROM stt_results sr
    JOIN files f ON sr.file_id = f.id
    WHERE f.user_id = :user_id
        AND sr.created_at BETWEEN :start_date AND :end_date + INTERVAL '1 day'
    ORDER BY sr.created_at ASC, sr.index ASC

    """
)

SELECT_IMAGE_FILES = text(
    """
SELECT image_path
FROM image_files imf
WHERE imf.user_id = :user_id 
  AND imf.start_date = :start_date
  AND imf.end_date = :end_date
  AND imf.type = :type;
"""
)

SELECT_IMAGE_TYPE = text(
    """
SELECT DISTINCT type
FROM image_files
WHERE user_id = :user_id
  AND start_date = :start_date
  AND end_date = :end_date;
"""
)

SENTENCE_COUNT = text(
    """
    SELECT speaker_label, COUNT(*) AS sentence_count
    FROM stt_results
    GROUP BY speaker_label;
    """
)

TOTAL_SENTEMCES = text(
    """
    SELECT COUNT(*) AS total_sentences
    FROM stt_results;
    """
)

CHAR_COUNTS = text(
    """
    SELECT speaker_label, SUM(LENGTH(text_edited)) AS total_characters
    FROM stt_results
    GROUP BY speaker_label;
    """
)

AVERAGE_SENTENCE_LENGTH = text(
    """
    SELECT speaker_label, AVG(LENGTH(text_edited)) AS avg_sentence_length
    FROM stt_results
    GROUP BY speaker_label;
    """
)

MAX_SENTENCE_LENGTH = text(
    """
    SELECT speaker_label, MAX(LENGTH(text_edited)) AS max_sentence_length
    FROM stt_results
    GROUP BY speaker_label;
    """
)

MIN_SENTENCE_LENGTH = text(
    """
    SELECT speaker_label, MIN(LENGTH(text_edited)) AS min_sentence_length
    FROM stt_results
    GROUP BY speaker_label;
    """
)

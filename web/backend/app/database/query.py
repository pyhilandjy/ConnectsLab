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
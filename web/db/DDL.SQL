CREATE TABLE users
(
    id varchar(255) NOT NULL,
    user_name varchar(255) NOT NULL,
    role_id int,
    plan_id int,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
);

CREATE TABLE files
(
    id varchar(255) NOT NULL,
    user_id varchar(255) NOT NULL,
    file_name varchar(255) NOT NULL,
    file_path varchar(255) NOT NULL,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
);


CREATE TABLE stt_results
(
    file_id varchar(255) NOT NULL,
    index int NOT NULL,
    start_time int NOT NULL,
    end_time int NOT NULL,
    text varchar(255) NOT NULL,
    confidence float NOT NULL,
    speaker_label int NOT NULL,
    text_edited varchar(255) NOT NULL,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (file_id, index)
);

CREATE TABLE roles
(
    id int NOT NULL,
    role_name varchar(255) NOT NULL,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
);

CREATE TABLE plans
(
    id int NOT NULL,
    plan_name varchar(255) NOT NULL,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
);

CREATE TABLE image_file
(
    id varchar(255) NOT NULL,
    user_id varchar(255) NOT NULL,
    start_date timestamp NOT NULL,
    end_date timestamp NOT null,
    image_path varchar(255) NOT NULL,
    PRIMARY KEY (id)
);
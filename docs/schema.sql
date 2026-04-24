CREATE TABLE staff (
	id INTEGER NOT NULL, 
	fio VARCHAR, 
	position VARCHAR, 
	degree VARCHAR, 
	email VARCHAR, 
	photo_url VARCHAR, 
	bio TEXT, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_staff_id ON staff (id);
CREATE INDEX ix_staff_fio ON staff (fio);
CREATE TABLE news (
	id INTEGER NOT NULL, 
	title VARCHAR, 
	content TEXT, 
	date DATETIME, 
	external_link VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (external_link)
);
CREATE INDEX ix_news_id ON news (id);
CREATE INDEX ix_news_title ON news (title);
CREATE TABLE materials (
	id INTEGER NOT NULL, 
	title VARCHAR, 
	author VARCHAR, 
	discipline VARCHAR, 
	description TEXT, 
	file_path VARCHAR, 
	preview_text TEXT, 
	external_link VARCHAR, 
	year INTEGER, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_materials_id ON materials (id);
CREATE INDEX ix_materials_title ON materials (title);
CREATE INDEX ix_materials_discipline ON materials (discipline);

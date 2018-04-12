create database conference_sea charset=utf8;

CREATE table organizers(
	id int UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
	url VARCHAR(100) UNIQUE NOT NULL,
	name VARCHAR(100)
)ENGINE = innodb;
# 组织为1, 会议为多
create table conferences (
	id int unsigned not null auto_increment primary key,
	title varchar(150) not null,
	url varchar(200) not null unique,
	start_date date,
	end_date date,
	area varchar(50),
	specialties varchar(100),
	organizer_id INT UNSIGNED,
	FOREIGN KEY (organizer_id) REFERENCES organizers(id)
)engine=innodb;

create table speakers(
	id int unsigned not null auto_increment primary key,
	name varchar(30) not null,
	url varchar(100) unique not null,
	position varchar(100),
	address VARCHAR(100),
	specialties varchar(300),
	interested varchar(300)
)engine=innodb;


create table conferences_speakers(
	id int unsigned auto_increment primary key,
	conference_id int unsigned,
	speakers_id int unsigned,
	foreign key(conference_id) references conferences(id),
	foreign key(speakers_id) references speakers(id)
)engine=innodb;

create TABLE organizers_speakers(
	id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	organizers_id INT UNSIGNED,
	speakers_id INT UNSIGNED,
	FOREIGN KEY (organizers_id) REFERENCES organizers(id),
	FOREIGN KEY (speakers_id) REFERENCES speakers(id)
)engine=innodb;
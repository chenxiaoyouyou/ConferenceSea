create database conference_sea charset=utf8;

create table conference (
	id int unsigned not null auto_increment primary key,
	title varchar(150) not null,
	url varchar(200) not null unique,
	start_date date,
	end_date date,
	area varchar(50),
	organized varchar(100),
	specialties varchar(100)
)engine=innodb;

create table speakers(
	id int unsigned not null auto_increment primary key,
	name varchar(30) not null,
	url varchar(100) unique not null,
	position varchar(100),
	specialties varchar(100),
	interested varchar(200)
)engine=innodb;


create table conference_speakers(
	id int unsigned auto_increment primary key,
	conference_id int unsigned,
	speakers_id int unsigned,
	foreign key(conference_id) references conference(id),
	foreign key(speakers_id) references speakers(id)
)engine=innodb;


alter table `product' add CONSTRAINT `sid_ref` FOREIGN KEY (`sid`) REFERENCES `sealer` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION 

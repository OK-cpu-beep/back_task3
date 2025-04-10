CREATE TABLE application (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  name varchar(128) NOT NULL DEFAULT '',
  year int(10) NOT NULL DEFAULT 0,
  ability_god int(1) NOT NULL DEFAULT 0,
  ability_fly int(1) NOT NULL DEFAULT 0,
  ability_idclip int(1) NOT NULL DEFAULT 0,
  ability_fireball int(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
);

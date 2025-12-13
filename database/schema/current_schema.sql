CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	password_hash VARCHAR(120) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);
CREATE TABLE patient (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	gender VARCHAR(10) NOT NULL, 
	birth_date DATE NOT NULL, 
	address VARCHAR(200) NOT NULL, phone TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE doctor (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE medicine (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	usage_method VARCHAR(200) NOT NULL, 
	description TEXT NOT NULL, 
	side_effects TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE visit (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	location VARCHAR(200) NOT NULL, 
	symptoms TEXT NOT NULL, 
	diagnosis VARCHAR(200) NOT NULL, 
	prescriptions_text TEXT NOT NULL, 
	patient_id INTEGER NOT NULL, 
	doctor_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id), 
	FOREIGN KEY(doctor_id) REFERENCES doctor (id)
);
CREATE TABLE prescription (
	id INTEGER NOT NULL, 
	visit_id INTEGER NOT NULL, 
	medicine_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(visit_id) REFERENCES visit (id), 
	FOREIGN KEY(medicine_id) REFERENCES medicine (id)
);

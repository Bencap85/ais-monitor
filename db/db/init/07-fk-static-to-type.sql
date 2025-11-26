ALTER TABLE ship_static_data
    ADD CONSTRAINT fk_ship_type
    FOREIGN KEY (ship_type)
    REFERENCES ship_type(type_code)
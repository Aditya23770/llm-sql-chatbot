-- Drop the customers table if it exists to ensure a clean start
DROP TABLE IF EXISTS customers;

-- Create a single customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    location VARCHAR(255)
);

-- Insert at least 5 sample entries
INSERT INTO customers (name, gender, location) VALUES
('Aisha Khan', 'Female', 'Mumbai'),
('Rohan Sharma', 'Male', 'Delhi'),
('Priya Singh', 'Female', 'Bangalore'),
('Arjun Mehta', 'Male', 'Mumbai'),
('Sneha Reddy', 'Female', 'Hyderabad'),
('Vikram Patel', 'Male', 'Ahmedabad'),
('Ananya Joshi', 'Female', 'Mumbai');
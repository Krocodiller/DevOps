-- LAB 8: Test migration for CI/CD automation
-- Adding test_field to patient table for pipeline testing
-- Date: 2025-12-13

ALTER TABLE patient ADD COLUMN test_field TEXT DEFAULT 'lab8_test';

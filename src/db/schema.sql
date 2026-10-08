CREATE TABLE IF NOT EXISTS documents (
    doc_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    domain ENUM('digital_lending', 'kyc','payment_aggregator') NOT NULL,
    doc_type ENUM('master_direction','circular','guideline','faq','press_release') NOT NULL,
    issue_date DATE NOT NULL,
    effective_date DATE,
    status ENUM('in_force','repealed','partially_superseded') NOT NULL,
    repeal_date DATE NULL,
    applies_to VARCHAR(300) NULL,
    source_url VARCHAR(1000) NULL,
    file_path VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    new_doc_id VARCHAR(100) NOT NULL,
    old_doc_id    VARCHAR(100) NOT NULL,
    relation_type ENUM('supersedes','amends','refers_to') NOT NULL,
    note VARCHAR(500) NULL,
    FOREIGN KEY (new_doc_id) REFERENCES documents(doc_id),
    FOREIGN KEY (old_doc_id) REFERENCES documents(doc_id)
);
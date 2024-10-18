PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
INSERT INTO users VALUES(2,'Angel','scrypt:32768:8:1$Oy5EoHVe0UEdT7XS$8553ca9ba32d2eb34409ca8cc92f5d421f126906643a51c829d2d1ac1c6332aeaafa85989323171d009370dca43ed2ac16f9e098f60512ee372dde2b2201b644');
INSERT INTO users VALUES(3,'Lucky','scrypt:32768:8:1$gvwcke1BlYp3q62u$6d40042ee160ec991eddfa01309e81b6d6537a42a3189b949c818572db1d6b12d29f3449d5185fc5f05e536ed9e92f6ac6fb33fdba5219f1d67ab741b7a842a6');
INSERT INTO users VALUES(4,'Loudrick','scrypt:32768:8:1$qcbsEHpTzLJaqqcS$037ec2841a52a5215a7fd1deed5a016e9cf797b4000448597e372ab2faca0ddd4c0db3dff6acecbff0a6652c70e797520f517d50e0176eb8d0dbebfd2547d3f8');
INSERT INTO users VALUES(6,'Lonwabo','scrypt:32768:8:1$BVFqEgj6uktarryR$5711712a996f6cc536d06a5d36d46b2102cc170fad251f5d32dbc276167aeb7d7d3ffdbd7870a51b3aa904d0a42fefb945401ff6272af0d90782ab2f0c4e6f3a');
CREATE TABLE discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic TEXT NOT NULL,
    discussion TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    discussion_id INTEGER,
    comment TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(discussion_id) REFERENCES discussions(id)
);
INSERT INTO comments VALUES(1,3,2,'or disease management, I''ve had good results with integrated pest management (IPM). Try introducing beneficial insects like ladybugs to control aphids naturally. Additionally, rotating your crops each season can help break the disease cycle.','2024-10-17 14:48:13');
INSERT INTO comments VALUES(2,3,2,'or disease management, I''ve had good results with integrated pest management (IPM). Try introducing beneficial insects like ladybugs to control aphids naturally. Additionally, rotating your crops each season can help break the disease cycle.','2024-10-17 14:49:57');
INSERT INTO comments VALUES(3,4,1,'I’ve used the hybrid ‘Pioneer 37Y40,’ which has shown excellent resistance to Common Rust. You can usually find it at local seed suppliers. Always check for updated resistance ratings before planting.','2024-10-17 14:51:10');
INSERT INTO comments VALUES(4,2,1,'Regarding Fall Armyworms, I recommend using a biological control like Bacillus thuringiensis (Bt). It’s safe for beneficial insects and very effective against caterpillars. Just be sure to apply it when the larvae are small for the best results.','2024-10-17 15:39:25');
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_name TEXT,
    disease_name TEXT,
    confidence_score REAL,
    recommendation TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
INSERT INTO classifications VALUES(7,2,'2024-10-17 17:41:40.650232','1729179696_3c423b70-c265-47ab-9aad-9f5235ccd343___RS_NLB 3819.JPG','Northern Leaf Blight',99.0,'Apply fungicides (e.g., azoxystrobin, pyraclostrobin, or propiconazole) early in the growing season when conditions are favorable for disease development.');
INSERT INTO classifications VALUES(8,3,'2024-10-17 17:42:40.198348','1729179759_3c423b70-c265-47ab-9aad-9f5235ccd343___RS_NLB 3819.JPG','Northern Leaf Blight',99.0,'Apply fungicides (e.g., azoxystrobin, pyraclostrobin, or propiconazole) early in the growing season when conditions are favorable for disease development.');
INSERT INTO classifications VALUES(9,3,'2024-10-17 17:43:23.665247','1729179803_05a7db2d-66b0-4a03-baad-730d04226aba___RS_NLB 4051.JPG','Northern Leaf Blight',99.0,'Apply fungicides (e.g., azoxystrobin, pyraclostrobin, or propiconazole) early in the growing season when conditions are favorable for disease development.');
INSERT INTO classifications VALUES(10,6,'2024-10-17 19:07:12.916836','1729184828_05a7db2d-66b0-4a03-baad-730d04226aba___RS_NLB 4051.JPG','Northern Leaf Blight',99.0,'Apply fungicides (e.g., azoxystrobin, pyraclostrobin, or propiconazole) early in the growing season when conditions are favorable for disease development.');

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    read INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',6);
INSERT INTO sqlite_sequence VALUES('classifications',10);
INSERT INTO sqlite_sequence VALUES('discussions',2);
INSERT INTO sqlite_sequence VALUES('comments',4);
COMMIT;

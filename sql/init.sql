-- drop table customer_t1;
-- User
CREATE TABLE "User" (
    uid int PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    usage INT NOT NULL -- gpu使用时长
);

-- 设备管理
CREATE TABLE gpu (
    gid int NOT NULL PRIMARY KEY,
    type varchar(255)
);

CREATE TABLE device(
    did int NOT NULL PRIMARY KEY,
    ip VARCHAR(255),
    cpu int NOT NULL , -- cpu核心数量
    cpu_name varchar(256), -- cpu型号
    memory int NOT NULL , -- 可用内存/MB
    data_dir varchar(256) NOT NULL , --机器数据盘位置
    pub_dir varchar(256) -- 公共数据位置（可选）
);

CREATE TABLE gpu_device (
    gid int not NULL,
    did int not NULL,
    FOREIGN KEY (gid) REFERENCES gpu(gid) ON DELETE CASCADE,
    FOREIGN KEY (did) REFERENCES device(did) ON DELETE CASCADE,
    PRIMARY KEY (gid, did)
);

--镜像管理

CREATE TABLE images (
    iid int not NULL, --镜像id
    did int not null, --设备id
    name VARCHAR(255) NOT NULL, --镜像名称
    real_id VARCHAR(255) NOT NULL, --镜像实际ID
    PRIMARY KEY (iid)
);

CREATE TABLE user_images (
    uid int not NULL,
    iid int not NULL,
    FOREIGN KEY (uid) REFERENCES "User"(uid) ON DELETE CASCADE,
    FOREIGN KEY (iid) REFERENCES images(iid) ON DELETE CASCADE
);  
--容器管理

CREATE TABLE containers(
    cid int not NULL,
    uid int NOT NULL,
    iid int NOT NULL,
    name varchar(255) NOT NULL,
    cpu int NOT NULL, -- cpu数量
    memory int NOT NULL, -- 内存大小，单位MB
    portssh int NOT NULL, -- ssh映射端口
    portjupyter int NOT NULL, -- jupyter映射端口
    porttsb int NOT NULL, -- tensorboard映射端口
    passwd VARCHAR(255) NOT NULL, -- ssh和jupyter访问密码
    status VARCHAR(10) NOT NULL, -- 状态：running, exited
    
    PRIMARY KEY (cid),
    FOREIGN KEY (uid) REFERENCES "User"(uid) ON DELETE CASCADE,
    FOREIGN KEY (iid) REFERENCES images(iid) ON DELETE CASCADE
);

CREATE TABLE container_gpu(
    cid int not NULL,
    gid int not NULL,
    FOREIGN KEY (cid) REFERENCES containers(cid) ON DELETE CASCADE,
    FOREIGN KEY (gid) REFERENCES gpu(gid) ON DELETE CASCADE
);
-- 查看结果
SELECT * FROM pg_tables where tableowner = 'superuser';
insert into "User" values
(1, 'root', '114514@163.com', 'matrixdl114514', 0);
insert into gpu values
(1, 'RTX4060 Ti 16GB');
insert into device values
(1, '172.18.198.204', 26, 'Intel(R) Core(TM) i7-14700K', 24576, '/home/node1/Desktop/code/db/matrixdl/container_data', '/home/node1/Desktop/code/ai/data/'); -- matrix-scc
insert into gpu_device values
(1, 1);
insert into images values
(1, 1, 'pytorch2.4.0-cuda11.8-cudnn9', '13ffa9344a0f')

insert into device values 
(2, '172.18.198.207', 4, 'Intel(R) Xeon(R) CPU E7-4830', 4096, '/home/matrixdl/container_data', NULL);-- matrixdl2
insert into images values
(2, 1, 'ubuntu', '7330f73882e8'),
(3, 2, 'ubuntu', '7330f73882e8');

-- tmp
insert into containers values
(1, 1, 1, 'test01', 2, 2048, 8001, 8002, 8003, '114514');
insert into containers values
(2, 1, 1, 'test01', 2, 2048, 8001, 8002, 8003, '114514');
select * from containers;
update containers set status = 'running' where cid = 1;
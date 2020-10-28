爬取天眼查数据
实现了自动登录
新建一个名字为 wky_oa 的数据库，导入sql数据

使用的话，在数据表kwy_corp_drafts里,添加name数据
比如
INSERT INTO `kwy_corp_drafts` (`id`, `guid`, `name`, `corp_avater`, `corptype`, `credit_code`, `birthday`, `summary`, `legal_person`, `phone`, `email`, `website`, `address`, `reg_address`, `status`, `industry`, `staff_size`, `business`, `is_new_tech`, `trademark_number`, `patent_number`, `copyright_number`, `is_pull`, `pull_time`, `created_id`, `created_time`) VALUES (NULL, '', '拼多多', '', '1', '', '0000-00-00', NULL, '', '', '', '', '', '', '', '', '', NULL, '0', '0', '0', '0', '0', '0000-00-00 00:00:00.000000', '0', '0000-00-00 00:00:00.000000');
再运行文件就可以了



必须改的地方
*数据库连接设置在19行和257行
*账号密码在577行修改
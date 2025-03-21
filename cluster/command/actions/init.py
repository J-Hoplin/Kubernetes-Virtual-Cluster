import os
import sys
import json
import sqlite3
import re
from cluster.constant import CLUSTER_PATH, SQLITE_PATH

def run(args):
	if not os.path.exists(args.config):
		print(f"Unable to find configuration file: {args.config}")
		return 1

	try:
		with open(args.config,'r') as f:
			config = json.load(f)
	except json.JSONDecodeError as e:
		print(f"JSON format error: {e.msg}")
		print(f"Line: {e.lineno}, Signature: {e.colno}")
		return 1

	db_path = SQLITE_PATH
	if getattr(sys, 'frozen', False):
		base_path = os.path.dirname(sys.executable)
	else:
		base_path = CLUSTER_PATH

	db_exist = os.path.exists(db_path) and os.path.getsize(db_path) > 0
	if db_exist:
		try:
			connection = sqlite3.connect(db_path)
			cursor = connection.cursor()
			cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='nodes'")
			if cursor.fetchone():
				cursor.execute("SELECT COUNT(*) FROM nodes")
				count = cursor.fetchone()[0]
				"""
				만약 기존에 관리하고 있던 cluster가 있는 경우
				Y: State 밀고 초기화, 단 이후 Manage 상태는 책임지지 않음
				N 혹은 다른거: 초기화 x
				"""
				if count > 0:
					if not args.force:
						print(f"Warning: {count} nodes are already registered.")
						confirmation = input("Do you want to delete existing cluster state and reinitialize? (y/N): ")
						if confirmation.lower() != 'y':
							print("Unable to proceed with existing cluster data.")
							connection.close()
							return 1
			connection.close()
		except sqlite3.Error as e:
			print(f"Error while checking database: {e}")
			print(f"SQLite ErrorName: {e.sqlite_errorname}({e.sqlite_errorcode})")
			return 1

	# 없는 경우에는 생성
	try:
		connection = sqlite3.connect(db_path)
		cursor = connection.cursor()
		node_type = ('master', 'worker')
		cursor.execute("DROP TABLE IF EXISTS nodes")
		cursor.execute(f"""
		CREATE TABLE nodes (
		    id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            node_type TEXT NOT NULL CHECK(node_type IN {node_type}),
            cpu INTEGER NOT NULL,
            memory INTEGER NOT NULL,
            disk INTEGER NOT NULL,
            ip TEXT,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		""")

		master_node_count = 0
		worker_node_count = 0
		for node_name, node_config in config.items():
			if not re.match(r'^[A-Za-z0-9][A-Za-z0-9-]*$',node_name):
				print(f"Error: Invalid node name: {node_name}")
				return 1
			node_type = node_config.get('type',"").lower()
			if node_type not in node_type:
				print(f"Error: Node type must be either 'master' or 'worker'")
				connection.close()
				return 1

			if node_type == 'master':
				master_node_count += 1
			else:
				worker_node_count += 1

			# Default value
			cpu = 2 if node_type == 'master' else 1
			memory = 2048 if node_type == 'master' else 1024
			disk = 10
			try:
				"""
				고정으로
				
				Memory는 MB단위
				Disk는 GB단위
				"""

				cpu = int(node_config.get("cpu",cpu))
				memory = int(node_config.get("memory",memory))
				disk = int(node_config.get("disk",disk))

			except ValueError as e:
				print(f"Error: Invalid value found while initializing node: {node_name}")
				print("Hint: CPU, Memory, Disk must be integer values")
				connection.close()
				return 1
			cursor.execute("""
					INSERT INTO nodes (name, node_type, cpu, memory, disk, ip, token)
					VALUES (?, ?, ?, ?, ?, ?, ?)
					""", (
				node_name,
				node_type,
				cpu,
				memory,
				disk,
				node_config.get("ip", ""),
				node_config.get("token", "")
			))
			if master_node_count == 0:
				print("Error: Kubernetes cluster must have at least one master node.")
				connection.close()
				return 1

			print(f"""
Cluster successfully initialized.

Master Node: {master_node_count}
Worker Node: {worker_node_count}
			""")
	except sqlite3.Error as e:
		print(f"Error while initializing database: {e}")
		print(f"SQLite ErrorName: {e.sqlite_errorname}({e.sqlite_errorcode})")
		return 1
	except Exception as e:
		print(f"Programmatic Error: {e}")
		print(f"Contact: hoplin.dev@gmail.com")
		return 1


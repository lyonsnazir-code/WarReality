import logging, os, sys

log_file = os.path.expanduser('~/genesis_node_00/core/genesis.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_node():
    logging.info('Executing Node 00 Health Audit...')
    checks = {
        'Data_Dir': os.path.exists(os.path.expanduser('~/genesis_node_00/data')),
        'DuckDB_State': os.path.exists(os.path.expanduser('~/genesis_node_00/data/ticks.duckdb')),
        'Blade_Engine': os.path.exists(os.path.expanduser('~/genesis_node_00/scripts/blade_anomaly.py'))
    }
    for k, v in checks.items():
        status = 'PASS' if v else 'FAIL'
        logging.info(f'Component [{k}]: {status}')
        print(f'[NODE HEALTH] {k}: {status}')

if __name__ == '__main__':
    audit_node()

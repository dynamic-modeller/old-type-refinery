import basic_logs as classic
import datetime
from typedb.client import *
from loguru import logger
import os

def load_footprint_types(session):
    footprint_types = ['insert $a isa footType; $a "->";',
            'insert $b isa footType; $b "<-";',
            'insert $c isa footType; $c "||";',
            'insert $d isa footType; $d "#";']
    for foot in footprint_types:            
        with session.transaction(TransactionType.WRITE) as write_transaction:
            insert_iterator = write_transaction.query().insert(foot)
            for concept_map in insert_iterator:
                concepts = concept_map.concepts()
                #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
            ## to persist changes, write transaction must always be committed (closed)
        write_transaction.commit()
            

def load_classic_logs(session, log, name):
    # setup the log entity
    graql_insert = 'insert $a isa log, has logName "'+name+'";'
    with session.transaction(TransactionType.WRITE) as write_transaction:
        insert_iterator = write_transaction.query().insert(graql_insert)
        for concept_map in insert_iterator:
            concepts = concept_map.concepts()
            #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
        ## to persist changes, write transaction must always be committed (closed)
        write_transaction.commit()
    # setup the trace relations
    logger.debug('====================== completed logname loading, now load log =======================================')
        
    for i, trace in enumerate(log):
        logger.debug(f' per log trace -> {trace}')
        prev_name = None
        for j, event_name in enumerate(trace):
            logger.debug('----------------------per trace ---------------------------------------------')
            trace_len = len(trace)
            #insert the event and trace on the log
            graql_insert = 'match $a isa log, has logName "'+name+'";'
            graql_insert += ' insert $b isa event, has eventName "'+event_name+'";'
            graql_insert += '  $c (owner: $a, item: $b) isa trace, '
            graql_insert += 'has traceId "'+name+str(i)+'", has index '+str(j)+';'
            logger.debug('graql insert {graql_insert}')
            with session.transaction(TransactionType.WRITE) as write_transaction:
                insert_iterator = write_transaction.query().insert(graql_insert)
                for concept_map in insert_iterator:
                    concepts = concept_map.concepts()
                    #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
                    #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
                    ## to persist changes, write transaction must always be committed (closed)
                    logger.debug("------ Insert Trace Statement")
                    logger.debug(f"Graql --> {graql_insert}")
                    logger.debug("------ Response")
                    for c in concepts:
                        if(c.is_attribute()):
                            logger.debug(c.get_value())
                        elif(c.is_relation()):
                            rel_id = c.get_iid()
                            logger.debug(f"relation id is {rel_id}")
                        else:
                            logger.debug(f"entity {c.get_iid()}")
                    logger.debug("------ End Trace Statement")
                    
                write_transaction.commit()
            
            if prev_name:
                graql_insert = 'match $a isa log, has logName "'+name+'";'
                graql_insert += '  $b isa event, has eventName "'+prev_name+'";'
                graql_insert += '  $c (owner: $a, item: $b) isa trace, '
                graql_insert += 'has traceId "'+name+str(i)+'", has index '+str(j-1)+';'
                graql_insert += '  $d isa event, has eventName "'+event_name+'";'
                graql_insert += '  $e (owner: $a, item: $d) isa trace, '
                graql_insert += 'has traceId "'+name+str(i)+'", has index '+str(j)+';'
                graql_insert += 'insert  $f (owner: $a, input: $b, output: $d) isa follows; '
                with session.transaction(TransactionType.WRITE) as write_transaction:
                    insert_iterator = write_transaction.query().insert(graql_insert)
                    for concept_map in insert_iterator:
                        concepts = concept_map.concepts()
                        #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
                        #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
                        ## to persist changes, write transaction must always be committed (closed)
                        logger.debug("------ Insert follows Relation Statement")
                        logger.debug(f"Graql --> {graql_insert}")
                        logger.debug("------ Response")
                        for c in concepts:
                            if(c.is_attribute()):
                                logger.debug(c.get_value())
                            elif(c.is_relation()):
                                rel_id = c.get_iid()
                                logger.debug(f"relation id is {rel_id}")
                            else:
                                logger.debug(f"concept {c.get_iid()}")
                        logger.debug("------ End Statement")

                    write_transaction.commit()
            
            prev_name = event_name
            if j == trace_len - 1:
                # insert the dummy end of trace event
                graql_insert = 'match $a isa log, has logName "'+name+'";'
                graql_insert += '  $b isa event, has eventName "'+event_name+'";'
                graql_insert += '  $c (owner: $a, item: $b) isa trace, '
                graql_insert += 'has traceId "'+name+str(i)+'", has index '+str(j)+';'
                graql_insert += '  $d isa event, has eventName "TraceStop";'
                graql_insert += 'insert  $f (owner: $a, input: $b, output: $d) isa follows; '
                with session.transaction(TransactionType.WRITE) as write_transaction:
                    insert_iterator = write_transaction.query().insert(graql_insert)
                    for concept_map in insert_iterator:
                        concept_map_list = concept_map.concepts()
                        for c_m in concept_map_list:
                            logger.debug(f"Inserted a concept with name: {c_m}")
                            #logger.debug("Inserted an event with name: {0}".format(concepts[0].id))
                            ## to persist changes, write transaction must always be committed (closed)
                            logger.debug("------ Insert follows Relation Statement")
                            logger.debug(f"Graql --> {graql_insert}")
                            logger.debug("------ Response")
                            if(c_m.is_attribute()):
                                logger.debug(c.get_value())
                            elif(c_m.is_relation()):
                                rel_id = c.get_iid()
                                logger.debug(f"relation id is {rel_id}")
                            else:
                                logger.debug(f"entity {c.get_iid()}")
                            logger.debug("------ End Statement")
                        
                    write_transaction.commit()



    
@logger.catch
def initialiselogs(server):
    typedb_connection = server["url"] + ":" + server["port"]
    with TypeDB.core_client(typedb_connection) as client:
        with client.session(server["database"], SessionType.DATA) as session:
            # insert null event
            graql_insert = 'insert  $a isa event, has eventName "TraceStop";'
            with session.transaction(TransactionType.WRITE) as write_transaction:
                    insert_iterator = write_transaction.query().insert(graql_insert)
                    for concept_map in insert_iterator:
                        concept_map_list = concept_map.concepts()
                        for c_m in concept_map_list:
                            logger.debug(f"Inserted a concept with name: {c_m}")
                    ## to persist changes, write transaction must always be committed (closed)
                    write_transaction.commit()
            # insert the raw activity names
            #load_footlogger.debug_types(session)
            load_classic_logs(session, classic.L1,'L1')
            load_classic_logs(session, classic.L2,'L2')
            load_classic_logs(session, classic.L3,'L3')
            load_classic_logs(session, classic.L4,'L4')
            load_classic_logs(session, classic.L5,'L5')
        
        
def main():
    server = {
        "url": os.environ.get('TYPEDB_HOST', 'localhost'),
        "port": os.environ.get('TYPEDB_PORT', '1729'),
        "database": os.environ.get('TYPEDB_DB', 'pm_4')
    }
    initialiselogs(server)


if __name__ == '__main__':
    main()
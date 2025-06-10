import sys
import os
sys.path.append('src')

from opendeepsearch.temporal_kg_tool import TemporalKGTool
from opendeepsearch.ods_tool import OpenDeepSearchTool

# Test if we can add the temporal tool to ODS
temporal_tool = TemporalKGTool(
    neo4j_uri="bolt://localhost:7687",
    username="neo4j", 
    password="maxx3169",
    model_name="test"
)

print("Temporal tool created successfully!")
print("Ready for ODS integration!") 
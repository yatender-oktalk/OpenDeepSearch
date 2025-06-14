import os

def test_environment():
    """Test if all required environment variables are set"""
    
    required_vars = {
        'NEO4J_URI': os.getenv('NEO4J_URI'),
        'NEO4J_USERNAME': os.getenv('NEO4J_USERNAME'),
        'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
        'TEMPORAL_KG_ENABLED': os.getenv('TEMPORAL_KG_ENABLED')
    }
    
    print("🔍 Environment Variables Check:")
    print("-" * 40)
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            print(f"✅ {var}: {'*' * len(value[:10])}...")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    if all_set:
        print("\n🎉 All environment variables are set!")
        
        # Test Neo4j connection
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                required_vars['NEO4J_URI'],
                auth=(required_vars['NEO4J_USERNAME'], required_vars['NEO4J_PASSWORD'])
            )
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                print("✅ Neo4j connection successful!")
            driver.close()
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
        
        # Test API key format
        api_key = required_vars['OPENROUTER_API_KEY']
        if api_key and len(api_key) > 20:
            print("✅ OpenRouter API key format looks valid")
        else:
            print("⚠️  OpenRouter API key might be invalid")
    
    else:
        print("\n❌ Please set missing environment variables before running evaluation")
    
    return all_set

if __name__ == "__main__":
    test_environment()

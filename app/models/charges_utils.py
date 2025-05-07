
from dataclasses import dataclass

@dataclass
class Payee:
    """Type-safe payee identifier"""
    entity_type: str  # 'vendor' or 'product'
    entity_id: int


    def __post_init__(self):
        
        if self.entity_type not in ('vendor', 'product'):
            raise ValueError("Entity type must be 'vendor' or 'product'")


    def __iter__(self):
        self.data = self.entity_type ,self.entity_id
        self.index = 0
  
        return self

    def __next__(self):
        
        if self.index >= len(self.data):
            raise StopIteration
        value = self.data[self.index]
        self.index += 1
        return value

def PayeeConstructor(entity_type: str, entity_id: int) -> Payee:
    """Factory function for creating Payee objects"""
    return Payee(entity_type.lower(), entity_id)
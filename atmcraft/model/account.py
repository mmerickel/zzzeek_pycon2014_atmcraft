
class Account(SurrogatePK, Base):
    __tablename__ = 'account'

    username = Column(String(20), nullable=False)
    balances = relationship(
                        "AccountBalance",
                        collection_class=attribute_mapped_collection("type")
                    )

    transactions = relationship("Transaction", backref="account")

    def add_transaction(self, type_, amount):
        balance_type = BalanceType.as_unique(session, name=type_)
        trans_id = uuid.uuid4()

        if balance_type in self.balances:
            account_balance = self.balances[balance_type]
        else:
            account_balance = AccountBalance()
        transaction = Transaction(
                            amount=amount,
                            balance_type=balance_type,
                            account_balance=account_balance)


class AccountBalance(SurrogatePK, Base):
    __tablename__ = 'account_balance'

    balance_type_id = ReferenceCol('balance_type')
    balance = Column(Amount)
    transaction_id = ReferenceCol("transaction")

class Transaction(SurrogatePK, Base):
    __tablename__ = 'transaction'

    trans_id = Column(UUID(), nullable=False, unique=True)
    client_id = ReferenceCol("client")
    account_balance_id = ReferenceCol("account_balance")
    amount = Column(Amount, nullable=False)


class BalanceType(UniqueMixin, SurrogatePK, Base):
    __tablename__ = 'balance_type'

    name = Column(String(50), nullable=False)

    @classmethod
    def unique_hash(cls, *arg, **kw):
        return cls.name

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        return query.filter(cls.name == kw['name'])

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

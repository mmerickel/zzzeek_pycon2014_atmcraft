========
ATMCRAFT
========

A demonstration Pyramid application written by Mike Bayer.

For the corresponding Minecraft Bukkit plugin, see
https://bitbucket.org/zzzeek/pycon2014_atmcraft_java/.

This program runs a simple web service which accepts
commands regarding "bank accounts".

The key database entities are:

* Client - represents a username/password that can log into
  the "atm"

* AuthSession - represents a specific login session for a Client

* Account - represents a set of balances on behalf of a Client

* AccountBalance - represents a specific balance (amount) for
  a certain type of asset (a BalanceType)

* BalanceType - represents a specifc kind of asset

* Transaction - represents a change in value to a specific AccountBalance

Usage
-----

- Clone the repository::

    git clone //bitbucket.org/zzzeek/pycon2014_atmcraft.git
    cd pycon2014_atmcraft

- Create a virtualenv::

    VENV=$(pwd)/venv
    virtualenv-2.7 $VENV

- Install the package and its dependencies::

    $VENV/bin/pip install -e .[tests]

- Update the ``development.ini`` to contain a valid connection string by either
  creating the user ``scott`` with password ``tiger`` or modifying the url.

- Create the postgresql database::

    createdb -O scott atmcraft

- Initialize the database::

    $VENV/bin/alembic -c development.ini upgrade head

- Execute the tests::

    TEST_INI=$(pwd)/development.ini $VENV/bin/nosetests

- Run the server::

    $VENV/bin/pserve development.ini

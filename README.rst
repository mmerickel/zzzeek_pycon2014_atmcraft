========
ATMCRAFT
========

A demonstration Pyramid application written by Mike Bayer.

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


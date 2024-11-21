
def generate_payment_address(self, label: str) -> str:
    """
    Generates a new Pepecoin payment address with the given label.

    :param label: A label to associate with the new address.
    :return: A new Pepecoin payment address.
    """
    try:
        payment_address = self.pepecoin_rpc.generate_new_address(label=label)
        return payment_address
    except Exception as e:
        print(f"Error generating payment address: {e}")
        return None
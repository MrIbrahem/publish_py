Before:

```python

class UsersNoInprocess:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        @self.bp.route("/", methods=["GET"])
        def dashboard():
            return _users_no_inprocess_dashboard()

        @self.bp.post("/add")
        @admin_required
        def add() -> ResponseReturnValue:
            return _add_user_no_inprocess()

        @self.bp.post("/<int:record_id>/delete")
        @admin_required
        def delete(record_id: int) -> ResponseReturnValue:
            return _delete_user_no_inprocess(record_id)

        @self.bp.post("/<int:record_id>/activate")
        @admin_required
        def activate(record_id: int) -> ResponseReturnValue:
            return _set_record_active_status(record_id, True)

        @self.bp.post("/<int:record_id>/deactivate")
        @admin_required
        def deactivate(record_id: int) -> ResponseReturnValue:
            return _set_record_active_status(record_id, False)

```

After:

```python

class UsersNoInprocess:
    def __init__(self, bp: Blueprint) -> None:
        self.bp = bp
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.bp.route("/", methods=["GET"])(self.dashboard) # example of no admin_required
        self.bp.post("/add")(admin_required(self.add))
        self.bp.post("/<int:record_id>/delete")(admin_required(self.delete))
        self.bp.post("/<int:record_id>/activate")(admin_required(self.activate))
        self.bp.post("/<int:record_id>/deactivate")(admin_required(self.deactivate))


    def dashboard(self):
        return _users_no_inprocess_dashboard()

    def add(self) -> ResponseReturnValue:
        return _add_user_no_inprocess()

    def delete(self, record_id: int) -> ResponseReturnValue:
        return _delete_user_no_inprocess(record_id)

    def activate(self, record_id: int) -> ResponseReturnValue:
        return _set_record_active_status(record_id, True)

    def deactivate(self, record_id: int) -> ResponseReturnValue:
        return _set_record_active_status(record_id, False)

```

Task: do the same for all class with `def _setup_routes(self) -> None:`

# this is not meant to be permanent
# it's just annoying to fill up en_model with a million type defs

# python is also annoying because it needs defs to happen in order of usage
# but the most intuitive ordering of defs in this context would break that

### type aliases (to make structure clearer)
loc_t = str
spec_t = str
enc_t = tuple[
    dict[spec_t, int],  # per-location mapping from species to encounter frequency
    spec_t | None,  # per-location canon encounter (if caught)
]
member_t = tuple[loc_t, spec_t]


### this is scuffed (rust-styled enums would make this much simpler)
from dataclasses import dataclass, field


@dataclass
class ToParty:
    """change status for some member to party (either new or from boxed)"""

    member: member_t
    """who is being placed in party"""
    is_new: bool  # should never be true when party is full
    """true if new, false if moved --> true should also set the canon encounter"""
    # straightforward recovery (move back to boxed/unmark catch)


@dataclass
class ToBoxed:
    """change status for some member to boxed (either new or from party)"""

    member: member_t
    """who is being placed in box"""
    is_new: bool  # should always be true when party is full
    """true if new, false if moved --> true should also set the canon encounter"""
    # straightforward recovery (move back to party/unmark catch)


@dataclass
class PartyToDead:
    """change status for some member to dead (from party)"""

    member: member_t
    """who is being placed in cemetery"""
    # never is_new: only moved from party (see FailEnc to fail an encounter)
    # straightforward recovery (move back to party)


@dataclass
class FailedCanonEnc:
    """mark the current/most recent encounter as canon without catch"""

    member: member_t
    """what/where was the failed encounter"""
    # straightforward recovery (unset canon encounter)
    # that said, this shouldn't be queued up if a canon encounter is already set
    # in the current location -- when handling inputs/automarking, this should be
    # verified before processing this action


# TODO outline/add infrastructure for handling gift pokemon/other free encounters


# this one should only be necessary for tokens, which may not be relevant to all users
# thus we probably don't have to deal with updating canon listings
@dataclass
class EditEnc:
    """replace the species associated with a specific encounter"""

    old_member: member_t
    new_member: member_t


action_t = ToParty | ToBoxed | PartyToDead | FailedCanonEnc | EditEnc

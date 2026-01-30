#include "user.pb.h" // From gen/cpp
#include "utils.h"   // From libs/cpp/user_utils
#include <iostream>

int main() {
  // Use Generated Proto
  pithos::common::User u;
  u.set_name("Alex");
  u.set_id(101);

  // Use Shared Lib
  std::cout << user_utils::GetWelcomeMessage(u.name()) << std::endl;
  std::cout << "User ID: " << u.id() << std::endl;

  return 0;
}
